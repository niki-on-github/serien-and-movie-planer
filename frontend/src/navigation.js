import LiveTv from "@mui/icons-material/LiveTv";
import MovieFilter from "@mui/icons-material/MovieFilter";
import SaveAs from "@mui/icons-material/SaveAs";
import Home from "@mui/icons-material/Home";

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
    text: 'Editor',
    path: '/editor',
    icon: <SaveAs />
  }
];
