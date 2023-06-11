import List from "@mui/material/List";
import Drawer from "@mui/material/Drawer";
import Divider from "@mui/material/Divider";
import ListItem from "@mui/material/ListItem";
import ListItemButton from "@mui/material/ListItemButton";
import ListItemIcon from "@mui/material/ListItemIcon";
import ListItemText from "@mui/material/ListItemText";
import AppBar from "@mui/material/AppBar";
import Toolbar from "@mui/material/Toolbar";
import Typography from "@mui/material/Typography";
import Box from "@mui/material/Box";
import IconButton from "@mui/material/IconButton";
import MenuIcon from "@mui/icons-material/Menu";
import * as React from "react";
import { navigation } from "../navigation";
import Avatar from "@mui/material/Avatar";
import { NavLink } from "react-router-dom";
import { useNavigation } from "../contexts/navigation";
import styled from "styled-components";
import useWindowDimensions from "../contexts/WindowDimension";
import useAppbarHeight from "../contexts/AppBarHeight";
import { createTheme } from "@mui/material/styles";

const StyledLink = styled(NavLink)`
  color: black;
  text-decoration: none;
  flex: 1;
  font-weight: "bold";

  &.active {
    color: white;
    background-color: #2196f3;
  }
`;

export default function DashboardLayout({ children }) {
const theme = createTheme();
  const { height, width } = useWindowDimensions();
  const appbarHeight = useAppbarHeight();
  const [drawerState, setDrawerState] = React.useState(false);
  const {
    navigationData: { currentPath },
  } = useNavigation();
  const toggleDrawer = (open) => (event) => {
    if (
      event.type === "keydown" &&
      (event.key === "Tab" || event.key === "Shift")
    ) {
      return;
    }

    setDrawerState(open);
  };

  function capitalizeFirstLetter(string) {
    return string.charAt(0).toUpperCase() + string.slice(1);
  }

  return (
    <>
      <Box sx={{ flexGrow: 1 }}>
        <AppBar position="static">
          <Toolbar>
            <IconButton
              size="large"
              edge="start"
              color="inherit"
              aria-label="menu"
              sx={{ mr: 2 }}
              onClick={toggleDrawer(true)}
            >
              <MenuIcon />
            </IconButton>
            <Typography variant="h6" component="div" sx={{ flexGrow: 1 }}>
              {capitalizeFirstLetter(currentPath.substring(1))}
            </Typography>
          </Toolbar>
        </AppBar>
      </Box>
      <Box sx={{ flexGrow: 1, m: 1 }} />
      <Drawer anchor={"left"} open={drawerState} onClose={toggleDrawer(false)}>
        <Box
          sx={{ width: 250 }}
          role="presentation"
          onClick={toggleDrawer(false)}
          onKeyDown={toggleDrawer(false)}
        >
          <Box
            display="flex"
            justifyContent="center"
            alignItems="center"
            sx={{ flexGrow: 1, mt: 2, mb: 1, ml: -1 }}
          >
            <Avatar src="logo.png" sx={{ width: 90, height: 90 }} />
          </Box>
          <Divider />
          <List>
            {navigation.map((item) => (
              <ListItem key={item.text} disablePadding>
                <StyledLink to={item.path}>
                  <ListItemButton>
                    <ListItemIcon sx={{ ml: 1.5 }} style={{ color: "inherit" }}>
                      {item.icon}
                    </ListItemIcon>
                    <ListItemText
                      primary={<Typography>{item.text}</Typography>}
                    />
                  </ListItemButton>
                </StyledLink>
              </ListItem>
            ))}
          </List>
        </Box>
      </Drawer>
      <Box height={height - appbarHeight - theme.spacing(2).replace('px','')} sx={{ flexGrow: 1 }}>
        {children}
      </Box>
    </>
  );
}
