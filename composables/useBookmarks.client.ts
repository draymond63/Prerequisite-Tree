export const useBookmarks = () => {
  const { $Gun } = useNuxtApp();
  const bookmarks = $Gun.get('user').get('bookmarks');

  const state = reactive({ bookmarks: new Set<string>() });

  // Don't listen changes, only retrieve on startup
  bookmarks.map().once((status, title) => {
    if (typeof status == 'boolean' && status)
      state.bookmarks.add(title);
    else
      state.bookmarks.delete(title);
  });
  return state
}