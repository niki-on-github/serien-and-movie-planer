import { HomePage, Movies, Serien, Admin } from './pages';
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
