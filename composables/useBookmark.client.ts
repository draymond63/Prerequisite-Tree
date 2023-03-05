export const useBookmark = (title: string) => {
  const { $Gun } = useNuxtApp();
  const bookmark = $Gun.get('user').get('bookmarks').get(title);

  const state = reactive({ bookmarked: false });
  const update = (status: boolean) => bookmark.put(status);

  bookmark.on((status: boolean) => {
    if (typeof status == 'boolean')
      state.bookmarked = status;
  });
  return {
    state, 
    update,
  }
}