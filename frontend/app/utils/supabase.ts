import { createClient } from "@supabase/supabase-js";

const supabaseUrl = process.env.NEXT_SUPABASE_URL as string;
const supabaseKey = process.env.NEXT_SUPABSE_KEY as string;

export const supabase = createClient(supabaseUrl, supabaseKey);