<template>
  <li class="w-2/3 p-2">
    <NuxtLink :to="'/topic/' + title">
      <div class="w-full flex">
        <img class="w-32 h-32 m-1 mr-3 border-secondary border-8" src="https://picsum.photos/seed/picsum/600/400" alt="Placeholder" />
        <div class="h-min px-4 py-2 bg-white rounded-md shadow-lg shadow-slate-50">
          <h2>{{ title }}</h2>
          <p class="line-clamp-4">
            Control theory is a field of mathematics that deals with the control of dynamical systems
            in engineered processes and machines. The objective is to develop a model or algorithm
            governing the application of system inputs to drive the system to a desired state, while
            minimizing any delay, overshoot, or steady-state error and ensuring a level of control
            stability; often with the aim to achieve a degree of optimality.
          </p>
        </div>
      </div>
    </NuxtLink>
  </li>
</template>

<script lang="ts">
export default {
  props: {
    title: {
      type: String,
      required: true,
    },
  }
}
</script>