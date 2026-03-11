import { useEffect, useState } from "react";
import API from "./api";

import {
    Button,
    Container,
    Typography,
    Table,
    TableHead,
    TableRow,
    TableCell,
    TableBody,
    Paper,
    Link
} from "@mui/material";

export default function Cars() {

    const [cars, setCars] = useState([]);

    useEffect(() => {
        loadCars();
    }, []);

    async function loadCars() {
        const res = await API.get("/api/cars");
        setCars(res.data);
    }

    function logout() {
        localStorage.removeItem("token");
        window.location.href = "/login";
    }

    return (
        <Container maxWidth="xl" sx={{ mt: 4 }}>
            <Typography variant="h4" gutterBottom align="center">
                Car Listings
            </Typography>
            <Paper sx={{
                display: 'flex',
                justifyContent: 'center',
                overflow: 'hidden'
            }}>
                <Table sx={{
                    maxWidth: '1200px',  // или нужная вам ширина
                    width: '100%'
                }}>
                    <TableHead>
                        <TableRow>
                            <TableCell align="center">Brand</TableCell>
                            <TableCell align="center">Model</TableCell>
                            <TableCell align="center">Year</TableCell>
                            <TableCell align="center">Price</TableCell>
                            <TableCell align="center">Color</TableCell>
                            <TableCell align="center">Link</TableCell>
                        </TableRow>
                    </TableHead>

                    <TableBody>
                        {cars.map((c) => (
                            <TableRow key={c.id} hover>
                                <TableCell align="center">{c.brand}</TableCell>
                                <TableCell align="center">{c.model}</TableCell>
                                <TableCell align="center">{c.year}</TableCell>
                                <TableCell align="center">
                                    ¥{c.price?.toLocaleString()}
                                </TableCell>
                                <TableCell align="center">{c.color}</TableCell>
                                <TableCell align="center">
                                    <Link href={c.url} target="_blank">
                                        View
                                    </Link>
                                </TableCell>
                            </TableRow>
                        ))}
                    </TableBody>
                </Table>
            </Paper>
            <Button
                variant="contained"
                color="error"
                onClick={logout}
            >
                Logout
            </Button>
        </Container>
    );
}