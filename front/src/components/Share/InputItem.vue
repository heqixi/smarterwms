<template>
    <q-input
      dense
      outlined
      square
      autofocus
      :v-model="data"
      :label="label"
      :rules="rules"
    />
</template>
<script>

export default{
  name : "InputItem",
  props: ['data', 'label', 'rules']
}
</script>
