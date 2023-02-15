<template>
  <div>
    <header class="w-full static bg-primary p-2 flex justify-between">
      <nav>
        <NuxtLink to="/home">Logo</NuxtLink>
      </nav>
      <SearchBar />
      <div />
    </header>
    <div class="px-16 py-2">
      <slot />
    </div>
  </div>
</template>