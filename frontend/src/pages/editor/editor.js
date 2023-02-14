import Box from "@mui/material/Box";
import ListCard from "../../components/ListCard";
import Grid from "@mui/material/Grid";
import React, { useState, useEffect } from "react";
import MonacoEditor from "@uiw/react-monacoeditor";

export default function Editor() {
  return (
    <div sx={{ flexGrow: 1}}>
        <MonacoEditor
          language="markdown"
          value="# Example"
          options={{
            theme: "vs",
          }}
        />
    </div>
  );
}
