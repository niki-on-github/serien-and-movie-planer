import LiveTv from "@mui/icons-material/LiveTv";
import MovieFilter from "@mui/icons-material/MovieFilter";
import Home from "@mui/icons-material/Home";
import GpsFixedIcon from '@mui/icons-material/GpsFixed';
import AdminPanelSettings from '@mui/icons-material/AdminPanelSettings';

export const navigation = [
  {
    text: 'Home',
    path: '/home',
    icon: <Home />
  },
  {
    text: 'Movies',
    path: '/movies',
    icon: <MovieFilter />
  },
  {
    text: 'Serien',
    path: '/serien',
    icon: <LiveTv />
  },
  {
    text: 'Tracker',
    path: '/tracker',
    icon: <GpsFixedIcon />
  },
  {
    text: 'Admin',
    path: '/admin',
    icon: <AdminPanelSettings />
  }
];
