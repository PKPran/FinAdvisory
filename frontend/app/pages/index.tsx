import { useState, useEffect } from 'react';
import { supabase } from '../utils/supabase';
import UserList from '../components/UserList';
import Layout from '../layout';

interface User {
  UID: number;
  first_name: string;
  last_name: string;
}

export default function Home() {
  const [users, setUsers] = useState<User[]>([]);

  useEffect(() => {
    fetchUsers();
  }, []);

const fetchUsers = async () => {
    try {
        const { data, error } = await supabase.from<User>('users').select('*');
        if (error) {
            console.error('Error fetching users:', (error as unknown as Error).message);
        } else {
            setUsers(data || []);
        }
    } catch (error) {
        console.error('Error fetching users:', (error as Error).message);
    }
};
  return (
    <Layout>
      <div className="flex flex-col items-center justify-center h-screen">
        <h1 className="text-4xl font-bold mb-4">Welcome to FonAdvisory</h1>
        <p className="text-lg text-gray-600">Your trusted platform for CA consultation.</p>
        <div className="mt-8">
          <button className="px-6 py-3 bg-blue-500 text-white rounded-md shadow-lg hover:bg-blue-600">Get Started</button>
        </div>
      </div>
      <div>
        <h1 className="text-2xl font-bold my-4">Users</h1>
        <button className="px-4 py-2 bg-blue-500 text-white rounded-md shadow-lg hover:bg-blue-600" onClick={fetchUsers}>Fetch Users</button>
        <UserList users={users} />
      </div>
    </Layout>
  );
}
