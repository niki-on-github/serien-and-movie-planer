import Box from "@mui/material/Box";
import ListCard from "../../components/ListCard";
import { Typography } from '@mui/material';

export default function Home() {
  return (
    <>
      <Box
        display="flex"
        justifyContent="center"
        alignItems="center"
        minHeight="90vh"
        sx={{ flexGrow: 1, mt: 3, mb: 3 }}
      >
        <h3>Welcome to Serian and Movie Planer</h3>
      </Box>
    </>
  );
}
