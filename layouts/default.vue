<template>
  <div>
    <header class="w-full static bg-primary p-2 flex justify-between">
      <nav>
        <NuxtLink to="/home">Logo</NuxtLink>
      </nav>
      <SearchBar />
      <div />
    </header>
    <slot />
  </div>
</template>