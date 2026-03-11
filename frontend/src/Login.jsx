import { useState } from "react";
import API from "./api";

import {
    Container,
    TextField,
    Button,
    Typography,
    Paper,
    Box
} from "@mui/material";

export default function Login() {

    const [email, setEmail] = useState("");
    const [password, setPassword] = useState("");

    async function login() {

        const form = new URLSearchParams();

        form.append("username", email);
        form.append("password", password);

        const res = await API.post("/api/login", form, {
            headers: {
                "Content-Type": "application/x-www-form-urlencoded"
            }
        });

        const token = res.data.access_token;

        if (token) {

            localStorage.setItem("token", token);

            API.defaults.headers.common["Authorization"] =
                `Bearer ${token}`;

            window.location.href = "/";
        }
    }

    return (
        <Container maxWidth="sm" sx={{ mt: 10 }}>

            <Paper sx={{ p: 4 }}>

                <Typography variant="h4" gutterBottom>
                    Login
                </Typography>

                <Box sx={{ display: "flex", flexDirection: "column", gap: 2 }}>

                    <TextField
                        label="Email"
                        value={email}
                        onChange={(e) => setEmail(e.target.value)}
                    />

                    <TextField
                        label="Password"
                        type="password"
                        value={password}
                        onChange={(e) => setPassword(e.target.value)}
                    />

                    <Button
                        variant="contained"
                        onClick={login}
                    >
                        Login
                    </Button>

                </Box>

            </Paper>

        </Container>
    );
}