<template>
  <div>
    <header class="w-full static bg-primary p-2 flex justify-between sticky top-0 z-50">
      <nav>
        <NuxtLink to="/home">Logo</NuxtLink>
      </nav>
      <SearchBar />
      <div />
    </header>
    <div class="relative px-6 md:px-16 py-2">
      <slot />
    </div>
  </div>
</template>