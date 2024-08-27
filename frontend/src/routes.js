import { HomePage, Movies, Serien, Tracker, Admin } from './pages';
import { withNavigationWatcher } from './contexts/navigation';

const routes = [
    {
        path: '/home',
        element: HomePage
    },
    {
        path: '/movies',
        element: Movies
    },
    {
        path: '/serien',
        element: Serien
    },
    {
        path: '/tracker',
        element: Tracker
    },
    {
        path: '/admin',
        element: Admin
    }
];

export default routes.map(route => {
    return {
        ...route,
        element: withNavigationWatcher(route.element, route.path)
    };
});
