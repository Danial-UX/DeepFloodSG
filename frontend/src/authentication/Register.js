import React, { useState } from "react";
import { Link, useNavigate } from "react-router-dom";
import "./Register.css";

const Register = () => {
	const [username, setUsername] = useState("");
	const [password, setPassword] = useState("");
	const [error, setError] = useState("");
	const navigate = useNavigate();

	const handleRegister = async (e) => {
		e.preventDefault();
		setError(""); // Clear previous errors

		try {
			const response = await fetch(
				"http://localhost:8000/api/account/register/",
				{
					method: "POST",
					headers: {
						"Content-Type": "application/json",
					},
					body: JSON.stringify({ username, password }),
				}
			);

			if (!response.ok) {
				const errorData = await response.json();
				throw new Error(errorData.error || "Registration failed");
			}

			// console.log("Registration successful");
			navigate("/login"); // Redirect to login page
		} catch (error) {
			// console.error("Registration error:", error);
			setError(error.message); // Display error message
		}
	};

	return (
		<div className="register-container">
			<div className="deepfloodsg-header">DeepFloodSG</div>
			<div className="register-box">
				<h2>Register</h2>
				{error && <p className="error-message">{error}</p>}{" "}
				<form onSubmit={handleRegister}>
					<input
						type="text"
						placeholder="Username"
						className="register-input"
						value={username}
						onChange={(e) => setUsername(e.target.value)}
						required
					/>
					<input
						type="password"
						placeholder="Password"
						className="register-input"
						value={password}
						onChange={(e) => setPassword(e.target.value)}
						required
					/>
					<button type="submit" className="register-button">
						Register
					</button>
				</form>

        <hr className="divider-line" />
      
        <p className="register-link">
					Already have an account?
					<Link to="/login"> Login Here</Link>
				</p>
			</div>
		</div>
	);
};

export default Register;
