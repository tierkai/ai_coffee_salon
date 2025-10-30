# AI咖啡知识沙龙 - 数据库设计

## 数据库表结构

### 1. profiles (用户资料)
```sql
id UUID PRIMARY KEY (references auth.users)
username TEXT UNIQUE
full_name TEXT
avatar_url TEXT
bio TEXT
created_at TIMESTAMP DEFAULT NOW()
updated_at TIMESTAMP DEFAULT NOW()
```

### 2. salons (知识沙龙会话)
```sql
id UUID PRIMARY KEY DEFAULT gen_random_uuid()
title TEXT NOT NULL
description TEXT
creator_id UUID (references profiles.id)
protocol_type TEXT CHECK (protocol_type IN ('tea', 'xiaolongbao', 'coffee'))
status TEXT CHECK (status IN ('draft', 'active', 'completed', 'archived'))
topic TEXT
target_audience TEXT
start_time TIMESTAMP
end_time TIMESTAMP
max_participants INTEGER DEFAULT 10
created_at TIMESTAMP DEFAULT NOW()
updated_at TIMESTAMP DEFAULT NOW()
```

### 3. salon_participants (沙龙参与者)
```sql
id UUID PRIMARY KEY DEFAULT gen_random_uuid()
salon_id UUID (references salons.id)
user_id UUID (references profiles.id)
role TEXT CHECK (role IN ('creator', 'participant', 'observer'))
joined_at TIMESTAMP DEFAULT NOW()
```

### 4. agent_messages (智能体消息)
```sql
id UUID PRIMARY KEY DEFAULT gen_random_uuid()
salon_id UUID (references salons.id)
agent_role TEXT CHECK (agent_role IN ('host', 'expert', 'researcher', 'analyst', 'recorder', 'summarizer', 'knowledge_manager'))
message_type TEXT CHECK (message_type IN ('statement', 'question', 'evidence', 'summary', 'analysis'))
content TEXT NOT NULL
metadata JSONB (存储引用、证据、评分等)
parent_message_id UUID (references agent_messages.id)
created_at TIMESTAMP DEFAULT NOW()
```

### 5. user_messages (用户消息)
```sql
id UUID PRIMARY KEY DEFAULT gen_random_uuid()
salon_id UUID (references salons.id)
user_id UUID (references profiles.id)
content TEXT NOT NULL
reply_to_message_id UUID
created_at TIMESTAMP DEFAULT NOW()
```

### 6. knowledge_items (知识条目)
```sql
id UUID PRIMARY KEY DEFAULT gen_random_uuid()
salon_id UUID (references salons.id)
title TEXT NOT NULL
content TEXT NOT NULL
category TEXT CHECK (category IN ('truth', 'goodness', 'beauty', 'inspiration'))
tags TEXT[]
evidence_sources JSONB (存储来源链接、引用等)
quality_score FLOAT (0-1之间)
consensus_level FLOAT (0-1之间)
created_by TEXT (可以是agent或user_id)
created_at TIMESTAMP DEFAULT NOW()
updated_at TIMESTAMP DEFAULT NOW()
```

### 7. knowledge_graph_nodes (知识图谱节点)
```sql
id UUID PRIMARY KEY DEFAULT gen_random_uuid()
knowledge_item_id UUID (references knowledge_items.id)
label TEXT NOT NULL
node_type TEXT CHECK (node_type IN ('concept', 'fact', 'argument', 'evidence'))
properties JSONB
created_at TIMESTAMP DEFAULT NOW()
```

### 8. knowledge_graph_edges (知识图谱关系)
```sql
id UUID PRIMARY KEY DEFAULT gen_random_uuid()
source_node_id UUID (references knowledge_graph_nodes.id)
target_node_id UUID (references knowledge_graph_nodes.id)
relationship_type TEXT (如 'supports', 'contradicts', 'derives_from', 'relates_to')
strength FLOAT (0-1之间)
created_at TIMESTAMP DEFAULT NOW()
```

### 9. salon_summaries (沙龙总结)
```sql
id UUID PRIMARY KEY DEFAULT gen_random_uuid()
salon_id UUID (references salons.id)
summary_type TEXT CHECK (summary_type IN ('interim', 'final'))
content TEXT NOT NULL
key_insights JSONB
action_items JSONB
quality_metrics JSONB (共识度、证据覆盖率、创新度等)
generated_by TEXT (通常是'summarizer'智能体)
created_at TIMESTAMP DEFAULT NOW()
```

### 10. files (文件存储记录)
```sql
id UUID PRIMARY KEY DEFAULT gen_random_uuid()
salon_id UUID (references salons.id)
user_id UUID (references profiles.id)
file_name TEXT NOT NULL
file_path TEXT NOT NULL (Storage路径)
file_type TEXT
file_size INTEGER
mime_type TEXT
created_at TIMESTAMP DEFAULT NOW()
```

## Row Level Security (RLS) 策略

### profiles表
- SELECT: 公开可读
- UPDATE: 仅用户本人可更新自己的资料

### salons表
- SELECT: 公开可读已发布的沙龙
- INSERT: 认证用户可创建
- UPDATE: 仅创建者可更新
- DELETE: 仅创建者可删除

### salon_participants表
- SELECT: 沙龙参与者和创建者可查看
- INSERT: 认证用户可加入公开沙龙
- DELETE: 用户可退出沙龙

### agent_messages, user_messages表
- SELECT: 沙龙参与者可查看
- INSERT: agent_messages由Edge Function插入，user_messages由认证用户插入

### knowledge_items表
- SELECT: 公开可读
- INSERT: Edge Function或认证用户可插入
- UPDATE: Edge Function可更新质量评分

### 其他表
- 适当的RLS策略确保数据安全
