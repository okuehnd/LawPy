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


function QueryPage(){
    const [newQuery,setNewQuery] = useState('');
    const navigate = useNavigate();
    const [error,setError] = useState(null);

    const handleSubmit = () =>{
        console.log("Submitting Query:",newQuery);

        if (!newQuery.trim()) {
            setError('Query cannot be empty!');
            return;
        }

        // Send POST request to the backend to submit the comment
        fetch('http://localhost:8000/api/SubmitQuery', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ query: newQuery }),
        })
        .then((response) => {
            if (!response.ok) {
                throw new Error('Failed to submit query');
            }
            return response.json();
        })
        .then((data) => {
            //naviageto new  page

            navigate('/results', { state: { query: newQuery, results: data.results } });
        })
        .catch((err) => {
            setError(err.message);
            console.error(err);
        });
    };

    return (
        <div>
            <Box 
            sx={{
                backgroundColor: '#a83246', // Blue background
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
            <Box
                display="flex"
                flexDirection="column"
                alignItems="center"
                justifyContent="center"
                minHeight="100vh"
                padding={2}
            >
            <TextField
                label="Enter Your Legal Question"
                variant="outlined"
                required
                value={newQuery}
                onChange={(e) => setNewQuery(e.target.value)}
                rows={1}
                sx={{  width: '50%', marginBottom: '10px' }}
            />
            {error && (
                    <Typography variant="body2" color="error">
                        {error}
                    </Typography>
            )}
            <Button 
                variant="contained"
                color="#a83246"
                onClick={handleSubmit}
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
                Submit
            </Button>
            </Box>

        </div>
    )
}

export default QueryPage;