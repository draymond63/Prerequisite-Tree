export const useBookmarks = () => {
  const { $Gun } = useNuxtApp();
  const bookmarks = $Gun.get('user').get('bookmarks');

  const state = reactive({ bookmarks: new Set<string>() });

  bookmarks.map().on((status, title) => {
    if (typeof status == 'boolean' && status)
      state.bookmarks.add(title);
    else
      state.bookmarks.delete(title);
  });
  return state
}