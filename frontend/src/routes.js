import { HomePage, Movies, Serien } from './pages';
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
    }
];

export default routes.map(route => {
    return {
        ...route,
        element: withNavigationWatcher(route.element, route.path)
    };
});
