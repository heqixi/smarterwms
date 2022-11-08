<template>
  <div>
    <q-expansion-item v-for="(data, index) in dataList" :key="index">
      <q-item-section>
        {{ data.goods_class }}
      </q-item-section>
      <q-item-section>
        {{ data.creater }}
      </q-item-section>
      <q-item-section>
        {{ data.create_time }}
      </q-item-section>
      <q-item-section>
        <div class="row">
          <div class="col">
            <q-btn
              round
              color="primary"
              icon="add"
              @click.stop="addItem(data.id)"
            />
          </div>
          <div class="col">
            <q-btn
              round
              color="primary"
              icon="edit"
              @click="$emit('alterCategory', data.id)"
            />
          </div>
          <div class="col">
            <q-btn
              round
              color="primary"
              icon="delete"
              @click="$emit('deleteCategory', data.id)"
            />
          </div>
        </div>
      </q-item-section>
    </q-expansion-item>
  </div>
</template>

<script>
export default {
  name: "ExpandableItem",

  props: ["dataList"],
  methods: {
    addItem(parent_id) {
      this.$emit("addCategory", parent_id);
    },
    getClassName(classObjects) {
      return classObjects.map((object) => {return object.goods_class});
    }
  }
};
</script>
