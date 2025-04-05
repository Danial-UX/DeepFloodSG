import React, { useState } from "react";
import { Link, useNavigate } from "react-router-dom";
import "./Login.css";

function Login() {
	const [username, setUsername] = useState("");
	const [password, setPassword] = useState("");
	const [error, setError] = useState("");
	const navigate = useNavigate();

	const handleLogin = async (e) => {
		e.preventDefault();
		setError(""); // Clear previous errors

		try {
			const response = await fetch(
				"http://localhost:8000/api/account/login/",
				{
					method: "POST",
					headers: {
						"Content-Type": "application/json",
					},
					body: JSON.stringify({ username, password }),
					credentials: "include",
				}
			);

			if (!response.ok) {
				throw new Error("Invalid credentials");
			}

			const data = await response.json();
			// console.log("Login successful:", data);

			localStorage.setItem("accessToken", data.token.access);
			localStorage.setItem("refreshToken", data.token.refresh);

			navigate("/main");
		} catch (error) {
			console.error("Login error:", error);
			setError("Invalid username or password");
		}
	};

	return (
		<div className="login-container">
			<div className="deepfloodsg-header">DeepFloodSG</div>
			<div className="login-box">
				<h2>Login</h2>
				{error && <p className="error-message">{error}</p>}
				<form onSubmit={handleLogin}>
					<input
						type="text"
						placeholder="Username"
						className="login-input"
						value={username}
						onChange={(e) => setUsername(e.target.value)}
					/>
					<input
						type="password"
						placeholder="Password"
						className="login-input"
						value={password}
						onChange={(e) => setPassword(e.target.value)}
					/>
					<button type="submit" className="login-button">
						Login
					</button>
				</form>

				<hr className="divider-line" />

				<p className="login-link">
					Don't have an account?
					<Link to="/register"> Register Here</Link>
				</p>

				<p className="login-link">
					Developer?
					<Link to="http://localhost:8000/admin/"> Admin Site</Link>
				</p>
			</div>
		</div>
	);
}

export default Login;
