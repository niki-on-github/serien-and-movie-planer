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

export default function DashboardLayout({ children }) {
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

  let activeStyle = {
    textDecoration: "none",
  };

  let inactiveStyle = {
    textDecoration: "none",
  };

  function capitalizeFirstLetter(string) {
    return string.charAt(0).toUpperCase() + string.slice(1);
  }

  return (
    <>
      <Box sx={{ flexGrow: 1, ml: -1, mr: -1, mt: -1 }}>
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
            sx={{ flexGrow: 1, mt: 3, mb: 3 }}
          >
            <Avatar src="logo512.png" />
          </Box>
          <Divider />
          <List>
            {navigation.map((item) => (
              <NavLink
                to={item.path}
                style={({ isActive }) =>
                  isActive ? activeStyle : inactiveStyle
                }
              >
                <ListItem key={item.text} disablePadding>
                  <ListItemButton>
                    <ListItemIcon>{item.icon}</ListItemIcon>
                    <ListItemText primary={item.text} />
                  </ListItemButton>
                </ListItem>
              </NavLink>
            ))}
          </List>
        </Box>
      </Drawer>
      {children}
    </>
  );
}
