import { createClient } from '@supabase/supabase-js';

const supabaseUrl = "https://mvbxxuoonqaomwqdwsmk.supabase.co";
const supabaseAnonKey = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Im12Ynh4dW9vbnFhb213cWR3c21rIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NjE2NDYyMjcsImV4cCI6MjA3NzIyMjIyN30.OtLhEh5O3d3pxey9m2OTVCW6bU1R_HpfR_YvUqOqPbI";

export const supabase = createClient(supabaseUrl, supabaseAnonKey);

// Types
export interface Profile {
  id: string;
  username: string | null;
  full_name: string | null;
  avatar_url: string | null;
  bio: string | null;
  created_at: string;
  updated_at: string;
}

export interface Salon {
  id: string;
  title: string;
  description: string | null;
  creator_id: string;
  protocol_type: 'tea' | 'xiaolongbao' | 'coffee';
  status: 'draft' | 'active' | 'completed' | 'archived';
  topic: string | null;
  target_audience: string | null;
  start_time: string | null;
  end_time: string | null;
  max_participants: number;
  created_at: string;
  updated_at: string;
}

export interface AgentMessage {
  id: string;
  salon_id: string;
  agent_role: 'host' | 'expert' | 'researcher' | 'analyst' | 'recorder' | 'summarizer' | 'knowledge_manager';
  message_type: 'statement' | 'question' | 'evidence' | 'summary' | 'analysis';
  content: string;
  metadata: any;
  parent_message_id: string | null;
  created_at: string;
}

export interface UserMessage {
  id: string;
  salon_id: string;
  user_id: string;
  content: string;
  reply_to_message_id: string | null;
  created_at: string;
}
