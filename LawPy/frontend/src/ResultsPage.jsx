import React from 'react';
import './App.css'
import TextField from '@mui/material/TextField';
import { useNavigate, Link } from 'react-router-dom';
import {
  Typography,
  Button,
  Box,
  Container,
} from '@mui/material';
import { useState, useEffect } from 'react';
import { useLocation } from 'react-router-dom';


const ResultsPage = () => {
    // const [newQuery,setNewQuery] = useState('');
    // const navigate = useNavigate();
    const navigate = useNavigate();
    const routerLocation = useLocation();
    const { query, results } = routerLocation.state || {}; 
    const [error,setError] = useState(null);

    const handleNewQuery = () =>{
        navigate(`/`)
    };

    return (
        <div>
            <Box 
            sx={{
                backgroundColor: '#a83246', 
                padding: '20px 0',
                marginBottom: '30px',
                textAlign: 'center',
                color: 'white',
            }}
            >
                <Container>
                    <Typography 
                    variant="h3" 
                    component="h1" 
                    gutterBottom 
                    sx={{ fontWeight: 'bold' }}
                    >
                    LawPy
                    </Typography>
                    <Typography 
                    variant="h6" 
                    component="p" 
                    sx={{ fontSize: '18px' }}
                    >
                    Find New York Case Law that relates to your query!
                    </Typography>
                </Container>
            </Box>
            <Box display="flex" flexDirection="column" alignItems="center" gap={2} mt={4}>
            <Typography
            variant="h6"
            color="primary"
            sx={{
                opacity: 1,
                '&:hover': {
                color: 'black', 
                textDecoration: 'bold', 
                },
            }}
            >
            {query}
            </Typography>
            <Button 
                variant="contained"
                color="#a83246"
                onClick={handleNewQuery}
                sx={{
                    width: '30%',
                    maxWidth: 400,
                    backgroundColor: '#a83246',
                    color: 'white',
                    '&:hover': {
                        backgroundColor: '#8b293a',
                    },
                    }}
            >
                New Query
            </Button>
            </Box>
            <Box display="flex" flexDirection="column" alignItems="center" gap={2} mt={4}>
            {results && results.length > 0 ? (
                results.map((result) => (
                    <Box
                    // key={result.id}
                    border={1}
                    borderColor="grey.400"
                    borderRadius={2}
                    padding={2}
                    width="100%"
                    maxWidth={600}
                    sx={{ '&:hover': { boxShadow: 3 } }}
                    >
                    <Link
                        to={result.url}
                        style={{
                        textDecoration: 'none', 
                        display: 'block',
                        }}
                    >
                        <Typography
                        variant="h6"
                        color="primary"
                        sx={{
                            opacity: 1,
                            '&:hover': {
                            color: 'blue', 
                            textDecoration: 'underline', 
                            },
                        }}
                        >
                        {result.title}
                        </Typography>
                    </Link>
                
                    </Box>
                ))
                
            ) : <Typography variant="body1">No results found for your query.</Typography>}
            </Box>

        </div>
    )
}

export default ResultsPage;