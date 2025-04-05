export const logout = async () => {
    try {
        const refreshToken = localStorage.getItem('refreshToken');
        
        const response = await fetch("http://localhost:8000/api/account/logout/", {
            method: "POST",
            headers: {
                "Content-Type": "application/json",
            },
            body: JSON.stringify({ refresh: refreshToken }),
        });

        if (!response.ok) {
            throw new Error("Logout failed");
        }

        localStorage.removeItem('accessToken');
        localStorage.removeItem('refreshToken');
        
        return true;
    } catch (error) {
        console.error("Logout error:", error);
        return false;
    }
};