import Box from "@mui/material/Box";
import ListCard from "../../components/ListCard";
import Grid from "@mui/material/Grid";
import React, { useState, useEffect } from "react";

export default function Home() {
  let [movieInfo, setMovieInfo] = useState({});
  let [serienInfo, setSerienInfo] = useState({});

  useEffect(() => {
    fetch("/api/v1/movies/count")
      .then((response) => response.json())
      .then((data) => setMovieInfo(data));
  }, []);

  useEffect(() => {
    fetch("/api/v1/serien/count")
      .then((response) => response.json())
      .then((data) => setSerienInfo(data));
  }, []);

  return (
    <>
      <Box sx={{ flexGrow: 1, mt: 3, mb: 2, ml: 2, mr: 2 }}>
        <Grid container spacing={2}>
          <Grid item xs={12} sm={6}>
            <ListCard title="Movies" content={movieInfo} />
          </Grid>
          <Grid item xs={12} sm={6}>
            <ListCard title="Serien" content={serienInfo} />
          </Grid>
        </Grid>
      </Box>
    </>
  );

  // return (
  //   <>
  //     <Box
  //       display="flex"
  //       justifyContent="center"
  //       alignItems="center"
  //       minHeight="90vh"
  //       sx={{ flexGrow: 1, mt: 3, mb: 3 }}
  //     >
  //       <h3>Welcome to Serian and Movie Planer</h3>
  //     </Box>
  //   </>
  // );
}
