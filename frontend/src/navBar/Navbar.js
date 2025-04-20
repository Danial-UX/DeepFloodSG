import React from "react";
import { Link, useNavigate } from "react-router-dom";
import { FaRegUserCircle, FaSignOutAlt } from "react-icons/fa"; 
import { logout } from "../authentication/Logout";
import "./Navbar.css";

const Navbar = () => {
    const navigate = useNavigate();

    const handleLogoutClick = async () => {
        const success = await logout();
        if (success) {
            navigate('/login');
        }
    };

    return (
        <nav className="navbar">
            <h2 className="logo">DeepFlood SG</h2>
            <ul>
                <li><Link to="/main">HOME</Link></li>
                {/* <li><Link to="/main">MAP</Link></li> */}
                {/* <li><Link to="/exploration">DATA EXPLORATION</Link></li> */}
            </ul>
            <div className="navbar-right">
                <Link to="/main" class="no-underline">
                    <FaRegUserCircle className="profile-icon" />
                </Link>
                <FaSignOutAlt 
                    className="sign-out-icon" 
                    onClick={handleLogoutClick}
                />
            </div>
        </nav>
    );
};

export default Navbar;
