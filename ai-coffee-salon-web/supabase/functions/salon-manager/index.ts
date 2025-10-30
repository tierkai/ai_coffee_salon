Deno.serve(async (req) => {
    const corsHeaders = {
        'Access-Control-Allow-Origin': '*',
        'Access-Control-Allow-Headers': 'authorization, x-client-info, apikey, content-type',
        'Access-Control-Allow-Methods': 'POST, GET, OPTIONS',
        'Access-Control-Max-Age': '86400',
        'Access-Control-Allow-Credentials': 'false'
    };

    if (req.method === 'OPTIONS') {
        return new Response(null, { status: 200, headers: corsHeaders });
    }

    try {
        const { action, salon_data } = await req.json();

        const serviceRoleKey = Deno.env.get('SUPABASE_SERVICE_ROLE_KEY');
        const supabaseUrl = Deno.env.get('SUPABASE_URL');

        if (!serviceRoleKey || !supabaseUrl) {
            throw new Error('Supabase configuration missing');
        }

        const authHeader = req.headers.get('authorization');
        if (!authHeader) {
            throw new Error('No authorization header');
        }

        const token = authHeader.replace('Bearer ', '');
        
        // 获取用户信息
        const userResponse = await fetch(`${supabaseUrl}/auth/v1/user`, {
            headers: {
                'Authorization': `Bearer ${token}`,
                'apikey': serviceRoleKey
            }
        });

        if (!userResponse.ok) {
            throw new Error('Invalid token');
        }

        const userData = await userResponse.json();
        const userId = userData.id;

        if (action === 'create') {
            // 创建新沙龙
            const { title, description, protocol_type, topic, target_audience } = salon_data;

            if (!title || !protocol_type) {
                throw new Error('title and protocol_type are required');
            }

            // 插入沙龙记录
            const salonResponse = await fetch(`${supabaseUrl}/rest/v1/salons`, {
                method: 'POST',
                headers: {
                    'Authorization': `Bearer ${serviceRoleKey}`,
                    'apikey': serviceRoleKey,
                    'Content-Type': 'application/json',
                    'Prefer': 'return=representation'
                },
                body: JSON.stringify({
                    title,
                    description,
                    protocol_type,
                    topic,
                    target_audience,
                    creator_id: userId,
                    status: 'active',
                    start_time: new Date().toISOString()
                })
            });

            if (!salonResponse.ok) {
                const errorText = await salonResponse.text();
                throw new Error(`Failed to create salon: ${errorText}`);
            }

            const salonData = await salonResponse.json();
            const salon = salonData[0];

            // 将创建者添加为参与者
            await fetch(`${supabaseUrl}/rest/v1/salon_participants`, {
                method: 'POST',
                headers: {
                    'Authorization': `Bearer ${serviceRoleKey}`,
                    'apikey': serviceRoleKey,
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({
                    salon_id: salon.id,
                    user_id: userId,
                    role: 'creator'
                })
            });

            // 主持人开场消息
            await fetch(`${supabaseUrl}/rest/v1/agent_messages`, {
                method: 'POST',
                headers: {
                    'Authorization': `Bearer ${serviceRoleKey}`,
                    'apikey': serviceRoleKey,
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({
                    salon_id: salon.id,
                    agent_role: 'host',
                    message_type: 'statement',
                    content: `欢迎来到《${title}》知识沙龙！我是主持人，本次沙龙将采用${protocol_type === 'tea' ? '茶协议（深度传承）' : protocol_type === 'xiaolongbao' ? '小笼包协议（结构化装配）' : '咖啡协议（创新探索）'}进行。让我们开始精彩的知识旅程！`,
                    metadata: JSON.stringify({ protocol_type, session_start: new Date().toISOString() })
                })
            });

            return new Response(JSON.stringify({
                data: {
                    success: true,
                    salon
                }
            }), {
                headers: { ...corsHeaders, 'Content-Type': 'application/json' }
            });

        } else if (action === 'list') {
            // 获取沙龙列表
            const status = salon_data?.status || 'active';
            
            const response = await fetch(
                `${supabaseUrl}/rest/v1/salons?status=eq.${status}&order=created_at.desc&limit=20`,
                {
                    headers: {
                        'Authorization': `Bearer ${serviceRoleKey}`,
                        'apikey': serviceRoleKey
                    }
                }
            );

            if (!response.ok) {
                throw new Error('Failed to fetch salons');
            }

            const salons = await response.json();

            return new Response(JSON.stringify({
                data: { salons }
            }), {
                headers: { ...corsHeaders, 'Content-Type': 'application/json' }
            });

        } else {
            throw new Error('Invalid action. Use "create" or "list"');
        }

    } catch (error) {
        console.error('Salon management error:', error);

        return new Response(JSON.stringify({
            error: {
                code: 'SALON_MANAGEMENT_FAILED',
                message: error.message
            }
        }), {
            status: 500,
            headers: { ...corsHeaders, 'Content-Type': 'application/json' }
        });
    }
});
