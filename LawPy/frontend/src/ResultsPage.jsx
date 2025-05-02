import React from 'react';
import './App.css'
import TextField from '@mui/material/TextField';
import { useNavigate, Link } from 'react-router-dom';
import {
  Typography,
  Button,
  Box,
  Container,
  Divider
} from '@mui/material';
import { useState, useEffect } from 'react';
import { useLocation } from 'react-router-dom';


const ResultsPage = () => {
    // const [newQuery,setNewQuery] = useState('');
    // const navigate = useNavigate();
    const navigate = useNavigate();
    const routerLocation = useLocation();
    const { query, message } = routerLocation.state || {}; 
    const [error,setError] = useState(null);
    const [results, setResults] = useState([]);
    const [page,setPage] = useState(1);
    const [limit] = useState(10);
    const[totalPages,setTotalPages] = useState(1);
    const [totalResults,setTotalResults] = useState(0);

    useEffect(() => {
        fetchData();
    }, [page, query]);
    

    const fetchData = () => {
        const search = new URLSearchParams({ query, page, limit }).toString();
        fetch(`http://localhost:8000/api/results/?${search}`)
          .then(res => res.json())
          .then(data => {
            setResults(data.items);
            setTotalPages(data.totalPages);
            setTotalResults(data.totalItems);
          });
    };

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
            <Typography variant="h6" color="primary">
                {totalResults} results found for{' '}
                <Box component="span" sx={{ fontWeight: 'bold' }}>
                    {query}
                </Box>
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
                results.map((result,i) => (
                    <Box
                    key={i}
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
                    <Divider sx={{ mb: 0.5, opacity: 0.3 }} />
                    <div>
                        {result.matchedKeywords.join(' • ')}
                    </div>
                
                    </Box>
                ))
                
            ) : <Typography variant="body1">No results found for your query.</Typography>}
            </Box>
            <Box 
                sx={{
                    backgroundColor: 'rgba(168, 50, 70, 0.8)', 
                    padding: '10px 0',
                    marginBottom: '30px',
                    marginTop: '30px',
                    textAlign: 'center',
                    color: 'white',
                }}
            >
                <button onClick={() => setPage(p => Math.max(p - 1, 1))} disabled={page === 1}>
                Prev
                </button>
                <span> Page {page} of {totalPages} </span>
                <button onClick={() => setPage(p => Math.min(p + 1, totalPages))} disabled={page === totalPages}>
                Next
                </button>
            </Box>

        </div>
    )
}

export default ResultsPage;