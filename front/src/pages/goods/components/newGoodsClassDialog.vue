<template>
  <q-card class="shadow-24">
    <q-bar
      class="bg-light-blue-10 text-white rounded-borders"
      style="height: 50px"
    >
      <div>{{ $t("newtip") }}</div>
      <q-space />
      <q-btn dense flat icon="close" v-close-popup>
        <q-tooltip content-class="bg-amber text-black shadow-4">{{
          $t("index.close")
        }}</q-tooltip>
      </q-btn>
    </q-bar>
    <div class="row justify-between">
      <q-item-section class="col3 q-ml-lg ">
        父类别
      </q-item-section>
      <q-space/>
      <div class="col-7 q-mt-sm q-mr-sm" v-if="parentCategory != null">
        {{parentCategory.goods_class}}
      </div>
      <div class="col-7 q-mt-sm q-mr-sm" v-else>
        <q-select
            dense
            outlined
            square
            v-model="parent"
            :options="parentOptions"
            transition-show="scale"
            transition-hide="scale"
            :rules="[val => (val && val.length > 0) || error9]"
          />
      </div>
    </div>

    <q-card-section style="max-height: 325px; width: 400px" class="scroll">
      <q-input
        dense
        outlined
        square
        v-model="goodsClass"
        :label="$t('goods.view_goodslist.goods_class')"
        autofocus
        :rules="[val => (val && val.length > 0) || error1]"
        @keyup.enter="newDataSubmit()"
      />
    </q-card-section>
    <div style="float: right; padding: 15px 15px 15px 0">
      <q-btn
        color="white"
        text-color="black"
        style="margin-right: 25px"
        @click="newDataCancel()"
        >{{ $t("cancel") }}</q-btn
      >
      <q-btn color="primary" @click="newDataSubmit()">{{ $t("submit") }}</q-btn>
    </div>
  </q-card>
</template>

<script>

export default {
  name: "NewGoodsClassDialog",
  data() {
    return {
      parent: "",
      goodsClass: "",
      pathname: "goodsclass/",
      error1: this.$t("goods.view_class.error1")
    };
  },
  props: ["parentCategory", "parentOptions"],
  methods: {
    newDataSubmit() {
      let parent_id = "";
      if (this.parentCategory != null) {
        parent_id = this.parentCategory.id;
      } else if (this.parent != null) {
        parent_id = this.parent.id;
      }
      console.log("new category dialog newDataSubmit id, ", parent_id);
      this.$emit("addCategory", parent_id, this.goodsClass);
    },
    newDataCancel() {
      console.log("new data cancel");
      this.$emit("cancalDialog");
    },

  },
};
</script>
