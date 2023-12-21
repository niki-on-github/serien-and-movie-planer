import LiveTv from "@mui/icons-material/LiveTv";
import MovieFilter from "@mui/icons-material/MovieFilter";
import Home from "@mui/icons-material/Home";
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
    text: 'Admin',
    path: '/admin',
    icon: <AdminPanelSettings />
  }
];
