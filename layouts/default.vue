<template>
  <div>
    <header class="w-full bg-primary p-2 flex justify-between">
      <nav>
        <ul>
          <li><NuxtLink to="/home">Logo</NuxtLink></li>
          <!-- <li><NuxtLink to="/topic/1">Topic 1</NuxtLink></li>
          <li><NuxtLink to="/topic/2">Topic 2</NuxtLink></li> -->
        </ul>
      </nav>
      <SearchBar />
      <div />
    </header>
    <slot />
  </div>
</template>  