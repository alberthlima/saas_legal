<script setup>
// Página de Dashboard básica

definePage({
  name: 'dashboard',
  meta: {
    layout: 'default',
  },
})
</script>

<template>
  <div class="pa-4">
    <VRow>
      <VCol cols="12">
        <VCard>
          <VCardTitle>
            Dashboard
          </VCardTitle>
          <VCardText>
            Bienvenido al panel principal.
          </VCardText>
        </VCard>
      </VCol>
    </VRow>
  </div>
</template>

<style scoped>
</style>
