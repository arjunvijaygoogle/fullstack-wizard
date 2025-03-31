import { useState, useEffect } from "react";
import {
  CircularProgress,
  Box,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  Paper,
} from "@mui/material";

interface Account {
  id: number;
  number: string;
  userId: number;
}

interface ApiResponse {
  accounts?: Account[];
}

const TableComponent = () => {
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
        const data: ApiResponse = await res.json(); // Expecting JSON response
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
    <div className="p-4 border rounded-lg shadow-lg">
      <h2 className="text-xl font-bold mb-2">Accounts Data</h2>
      {loading ? (
        <Box sx={{ display: 'flex', justifyContent: 'center', alignItems: 'center', minHeight: 100 }}>
          <CircularProgress />
          <span className="ml-2">Loading...</span>
        </Box>
      ) : error ? (
        <p className="text-red-500">Error: {error}</p>
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
        <p className="text-gray-500">No accounts data available.</p>
      )}
    </div>
  );
};

export default TableComponent;