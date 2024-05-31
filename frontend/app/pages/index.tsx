import { useState } from 'react';
import { supabase } from '../utils/supabase';
import UserList from '../components/UserList';
import Layout from '../layout'

interface User{
    UID: number;
    first_name: string;
    last_name: string;

}

export default function Home() {
    const [users, setUsers] = useState<User[]>([]);
    const fetchUsers = async () => {
        const { data, error } = await supabase.from('users').select('*');
        if (error) console.error('Error fetching users:', error.message);
        else setUsers(data || []);
    };

    return (
        <div>
            <h1>User</h1>
            <button onClick={fetchUsers}>Fetch Users</button>
            <UserList users={users} />
        </div>
    );
}