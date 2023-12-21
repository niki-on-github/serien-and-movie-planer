import Box from "@mui/material/Box";
import Grid from "@mui/material/Grid";
import Button from '@mui/material/Button';
import ListItem from '@mui/material/ListItem';
import List from '@mui/material/List';
import Divider from '@mui/material/Divider';
import ListItemAvatar from '@mui/material/ListItemAvatar';
import ListItemIcon from '@mui/material/ListItemIcon';
import ListItemText from '@mui/material/ListItemText';
import React, { useState, useEffect } from "react";

export default function Home() {

  const handleFileUpload = (e: ChangeEvent<HTMLInputElement>) => {
    if (!e.target.files) {
      return;
    }
    const fileReader = new FileReader();
    fileReader.readAsText(e.target.files[0], "UTF-8");
    fileReader.onload = e => {
      var content = e.target.result;
      console.log("import", content);
      fetch("/api/v1/import", {
        credentials: "same-origin",
        mode: "same-origin",
        method: "post",
        headers: { "Content-Type": "application/json" },
        body: content
      });
    };
  };

  return (
    <>
      <div style={{ display: 'flex', justifyContent: 'center', alignItems: 'center' }}>
        <Box sx={{ width: '800px', mt: 3 }}>
          <List>
            <Divider />
            <ListItem
              secondaryAction={
                <Button variant="outlined" onClick={() => {
                  window.open(window.location.protocol + '//' + window.location.hostname + ":" + window.location.port + "/api/v1/export", "_blank").focus();
                }}>Export</Button>

              }
            >
              <ListItemText
                primary="Export Databse to JSON"
              />
            </ListItem>
            <Divider />
            <ListItem
              secondaryAction={
                <Button
                  component="label"
                  variant="outlined"
                >
                  Import
                  <input type="file" accept=".json" hidden onChange={handleFileUpload} />
                </Button>
              }
            >
              <ListItemText
                primary="Import JSON to Database"
              />
            </ListItem>
            <Divider />
          </List>
        </Box>
      </div>
    </>
  );
}
