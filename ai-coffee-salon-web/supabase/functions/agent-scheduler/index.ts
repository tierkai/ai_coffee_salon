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
        const { salon_id, user_message, agent_roles } = await req.json();

        if (!salon_id) {
            throw new Error('salon_id is required');
        }

        const serviceRoleKey = Deno.env.get('SUPABASE_SERVICE_ROLE_KEY');
        const supabaseUrl = Deno.env.get('SUPABASE_URL');

        if (!serviceRoleKey || !supabaseUrl) {
            throw new Error('Supabase configuration missing');
        }

        // 1. 如果有用户消息，先保存
        if (user_message) {
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

            // 保存用户消息
            await fetch(`${supabaseUrl}/rest/v1/user_messages`, {
                method: 'POST',
                headers: {
                    'Authorization': `Bearer ${serviceRoleKey}`,
                    'apikey': serviceRoleKey,
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({
                    salon_id,
                    user_id: userData.id,
                    content: user_message
                })
            });
        }

        // 2. 智能体调度逻辑
        const activeRoles = agent_roles || ['host', 'expert', 'researcher', 'analyst'];
        const agentResponses = [];

        // 主持人开场
        if (activeRoles.includes('host')) {
            const hostMessage = {
                salon_id,
                agent_role: 'host',
                message_type: 'statement',
                content: user_message 
                    ? `感谢您的提问。我将协调专家团队为您提供全面的见解。`
                    : `欢迎来到AI咖啡知识沙龙！我是主持人，将协调多位智能体专家为您服务。`,
                metadata: JSON.stringify({ timestamp: new Date().toISOString() })
            };

            await fetch(`${supabaseUrl}/rest/v1/agent_messages`, {
                method: 'POST',
                headers: {
                    'Authorization': `Bearer ${serviceRoleKey}`,
                    'apikey': serviceRoleKey,
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify(hostMessage)
            });

            agentResponses.push(hostMessage);
        }

        // 专家分析
        if (activeRoles.includes('expert')) {
            const expertMessage = {
                salon_id,
                agent_role: 'expert',
                message_type: 'analysis',
                content: user_message
                    ? `基于我的专业知识，这个话题涉及多个维度。让我为您分析：\n1. 技术层面的创新点\n2. 实践应用的可行性\n3. 潜在的挑战与机遇`
                    : `作为领域专家，我将为本次沙龙提供专业见解和最佳实践分享。`,
                metadata: JSON.stringify({ 
                    expertise_area: '知识管理与AI应用',
                    confidence_level: 0.85
                })
            };

            await fetch(`${supabaseUrl}/rest/v1/agent_messages`, {
                method: 'POST',
                headers: {
                    'Authorization': `Bearer ${serviceRoleKey}`,
                    'apikey': serviceRoleKey,
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify(expertMessage)
            });

            agentResponses.push(expertMessage);
        }

        // 研究员检索
        if (activeRoles.includes('researcher')) {
            const researcherMessage = {
                salon_id,
                agent_role: 'researcher',
                message_type: 'evidence',
                content: user_message
                    ? `我已检索相关资料，发现以下重要信息：\n• 相关研究表明...\n• 最新案例显示...\n• 业界专家观点...`
                    : `我将负责检索和整理相关文献、案例和数据，为讨论提供证据支撑。`,
                metadata: JSON.stringify({ 
                    sources_count: 3,
                    evidence_quality: 0.8
                })
            };

            await fetch(`${supabaseUrl}/rest/v1/agent_messages`, {
                method: 'POST',
                headers: {
                    'Authorization': `Bearer ${serviceRoleKey}`,
                    'apikey': serviceRoleKey,
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify(researcherMessage)
            });

            agentResponses.push(researcherMessage);
        }

        // 分析员评估
        if (activeRoles.includes('analyst')) {
            const analystMessage = {
                salon_id,
                agent_role: 'analyst',
                message_type: 'analysis',
                content: user_message
                    ? `从数据分析角度来看：\n✓ 论点的逻辑一致性较高\n✓ 证据覆盖率达标\n⚠ 建议补充更多实证数据`
                    : `我将对讨论内容进行逻辑分析、事实核验，确保结论的可靠性。`,
                metadata: JSON.stringify({ 
                    logic_score: 0.82,
                    evidence_coverage: 0.75
                })
            };

            await fetch(`${supabaseUrl}/rest/v1/agent_messages`, {
                method: 'POST',
                headers: {
                    'Authorization': `Bearer ${serviceRoleKey}`,
                    'apikey': serviceRoleKey,
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify(analystMessage)
            });

            agentResponses.push(analystMessage);
        }

        return new Response(JSON.stringify({
            data: {
                success: true,
                salon_id,
                responses: agentResponses,
                message: '智能体协作响应成功'
            }
        }), {
            headers: { ...corsHeaders, 'Content-Type': 'application/json' }
        });

    } catch (error) {
        console.error('Agent scheduling error:', error);

        return new Response(JSON.stringify({
            error: {
                code: 'AGENT_SCHEDULING_FAILED',
                message: error.message
            }
        }), {
            status: 500,
            headers: { ...corsHeaders, 'Content-Type': 'application/json' }
        });
    }
});
