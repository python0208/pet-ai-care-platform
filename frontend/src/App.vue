<template>
  <slot />
</template>

<style>
page {
  min-height: 100%;
  background: #edf7ff;
  color: #10172d;
  font-family: "PingFang SC", "Microsoft YaHei", sans-serif;
}

view,
text {
  box-sizing: border-box;
}

button {
  margin: 0;
  padding: 0;
  border: 0;
  border-radius: 0;
  background: transparent;
  line-height: 1;
}

button::after {
  border: 0;
}
</style>
