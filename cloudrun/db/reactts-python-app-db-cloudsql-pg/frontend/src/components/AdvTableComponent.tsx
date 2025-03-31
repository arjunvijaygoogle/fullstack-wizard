import { useState, useEffect } from "react";
import {
  AppBar,
  Toolbar,
  Typography,
  Button,
  IconButton,
  CircularProgress,
  Box,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  Paper,
  Container,
} from "@mui/material";
import MenuIcon from "@mui/icons-material/Menu";
import { createTheme, ThemeProvider } from "@mui/material/styles";

interface Account {
  id: number;
  number: string;
  userId: number;
}

interface ApiResponse {
  accounts?: Account[];
}

const theme = createTheme({
  palette: {
    primary: {
      main: '#1976d2', // Material UI's primary blue
    },
    secondary: {
      main: '#dc004e', // A contrasting pink
    },
    background: {
      default: '#f0f2f5', // Light gray background
      paper: '#fff',
    },
  },
  typography: {
    h6: {
      fontWeight: 600,
    },
  },
  components: {
    MuiAppBar: {
      styleOverrides: {
        root: {
          boxShadow: '0 2px 4px rgba(0,0,0,0.1)', // Subtle shadow
        },
      },
    },
    MuiTableContainer: {
      styleOverrides: {
        root: {
          borderRadius: 8, // Rounded corners for the table
          boxShadow: '0 1px 3px rgba(0,0,0,0.05)',
        },
      },
    },
  },
});

const AdvTableComponent = () => {
  const [accounts, setAccounts] = useState<Account[] | null>(null);
  const [loading, setLoading] = useState<boolean>(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const API_URL = import.meta.env.VITE_REACT_APP_API_URL || "http://localhost:5000/ping";
    const fetchAccounts = async () => {
      setLoading(true);
      setError(null);
      try {
        console.log(API_URL);
        const res = await fetch(API_URL + 'accounts');
        if (!res.ok) {
          throw new Error(`HTTP error! Status: ${res.status}`);
        }
        const data: ApiResponse = await res.json();
        setAccounts(data.accounts || null);
      } catch (err) {
        setError((err as Error).message);
      } finally {
        setLoading(false);
      }
    };

    fetchAccounts();
  }, []);

  return (
    <ThemeProvider theme={theme}>
      <AppBar position="static">
        <Toolbar>
          <IconButton
            size="large"
            edge="start"
            color="inherit"
            aria-label="menu"
            sx={{ mr: 2 }}
          >
            <MenuIcon />
          </IconButton>
          <Typography variant="h6" component="div" sx={{ flexGrow: 1 }}>
            Account Management
          </Typography>
          <Button color="inherit">Home</Button>
          <Button color="inherit">About</Button>
        </Toolbar>
      </AppBar>
      <Container maxWidth="md" sx={{ mt: 4 }}>
        <Typography variant="h4" component="h2" gutterBottom>
          Account List
        </Typography>
        {loading ? (
          <Box sx={{ display: 'flex', justifyContent: 'center', alignItems: 'center', minHeight: 100 }}>
            <CircularProgress />
            <span className="ml-2">Loading accounts...</span>
          </Box>
        ) : error ? (
          <Typography color="error">Error: {error}</Typography>
        ) : accounts && accounts.length > 0 ? (
          <TableContainer component={Paper}>
            <Table sx={{ minWidth: 300 }} aria-label="accounts table">
              <TableHead>
                <TableRow>
                  <TableCell>ID</TableCell>
                  <TableCell align="left">Number</TableCell>
                  <TableCell align="left">User ID</TableCell>
                </TableRow>
              </TableHead>
              <TableBody>
                {accounts.map((account) => (
                  <TableRow
                    key={account.id}
                    sx={{ '&:last-child td, &:last-child th': { border: 0 } }}
                  >
                    <TableCell component="th" scope="row">
                      {account.id}
                    </TableCell>
                    <TableCell align="left">{account.number}</TableCell>
                    <TableCell align="left">{account.userId}</TableCell>
                  </TableRow>
                ))}
              </TableBody>
            </Table>
          </TableContainer>
        ) : (
          <Typography color="textSecondary">No accounts data available.</Typography>
        )}
      </Container>
    </ThemeProvider>
  );
};

export default AdvTableComponent;