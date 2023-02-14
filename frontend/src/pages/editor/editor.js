import Box from "@mui/material/Box";
import ListCard from "../../components/ListCard";
import Grid from "@mui/material/Grid";
import React, { useState, useEffect } from "react";
import MonacoEditor from "@uiw/react-monacoeditor";
import useWindowDimensions from "../../contexts/WindowDimension";
import useAppbarHeight from "../../contexts/AppBarHeight";

export default function Editor() {
    const { height, width } = useWindowDimensions();
    const appbarHeight = useAppbarHeight();

  return (
    <MonacoEditor
      language="html"
      value="<h1>I ♥ react-monacoeditor</h1>"
      options={{
        theme: "vs",
      }}
    />
  );
}
