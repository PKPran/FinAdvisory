import React from "react";

interface User{
    UID: number;
    first_name: string;
    last_name: string;
}

interface UserListProps{
    users: User[];
}

const UserList = ({ users }: UserListProps) => {
    return (
        <ul>
            {users.map((user) => (
                <li key={user.UID}>
                    {user.first_name} {user.last_name}
                </li>
            ))}
        </ul>
    );
}

export default UserList;