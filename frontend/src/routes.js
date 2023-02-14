import { HomePage, Movies, Serien, Editor } from './pages';
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
        path: '/editor',
        element: Editor
    }
];

export default routes.map(route => {
    return {
        ...route,
        element: withNavigationWatcher(route.element, route.path)
    };
});
