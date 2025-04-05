import React from "react";
import { Link } from "react-router-dom";
import "./404.css";

const NotFound = () => {
	return (
		<div className="container">
			<div className="deepfloodsg-header">
				DeepFloodSG: Error - Page Not Found
			</div>
      <Link to="/main">
			<div className="box">
					<h3 className="link">Return to Home</h3>
			</div>
      </Link> 
		</div>
	);
};

export default NotFound;
