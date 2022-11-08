<template>
  <q-scroll-area style="height: 800px; max-width: 2000px;">
    <q-card class="q-mx-sm">
      <q-card-section>
        <PurchasingList
          :phase="phases.purchase"
          :items="goodsToPurchaseList"
          @itemRemove="removeItem"
          @nextPhase="moveToNexePhase"
          @prePhase="moveToPrePhase"
          @dumplicate="duplicateItem"
          @addGoods="onGoodsSelected"
        >
          <template v-slot:testSlot>
            <div>Testing</div>
          </template>
        </PurchasingList>
      </q-card-section>

      <q-card-section>
        <PurchasingList
          :phase="phases.waiting"
          :items="goodsWaitingList"
          @itemRemove="removeItem"
          @nextPhase="moveToNexePhase"
          @prePhase="moveToPrePhase"
          @dumplicate="duplicateItem"
        />
      </q-card-section>

      <q-card-section>
        <PurchasingList
          :phase="phases.sort"
          :items="goodsToSortedList"
          @itemRemove="removeItem"
          @nextPhase="moveToNexePhase"
          @prePhase="moveToPrePhase"
          @dumplicate="duplicateItem"
        />
      </q-card-section>

      <q-card-section>
        <PurchasingList
          :phase="phases.stock"
          :items="goodsInStockList"
          @itemRemove="removeItem"
          @nextPhase="moveToNexePhase"
          @prePhase="moveToPrePhase"
          @dumplicate="duplicateItem"
        />
      </q-card-section>
    </q-card>

    <!-- <q-card-section>
      <div
        v-for="supplier in purchasingListStore.getToPurchaseMap()"
        :key="supplier"
      >
        This is a test {{ supplier }}
      </div>
    </q-card-section> -->
  </q-scroll-area>
</template>

<script>
import PurchasingList from "./purchasingList.vue";
import { PurchaingListStore } from "../store/purchaingList.js";
import { mapGetters } from "vuex";

export default {
  name: "purchasingSteps",
  data() {
    return {
      goodsToPurchaseList: [],
      goodsWaitingList: [],
      goodsToSortedList: [],
      goodsInStockList: [],
      purchasingListStore: undefined,
      phases: undefined
    };
  },
  computed: {

  },
  created() {
    this.purchasingListStore = new PurchaingListStore(
      this.goodsToPurchaseList,
      this.goodsWaitingList,
      this.goodsToSortedList,
      this.goodsInStockList
    );
    this.phases = this.purchasingListStore.getPhases();
    // for test
    let testGoods = [
      {
        goods_code: "goods_code 2 ",
        image_url: "https://cdn.quasar.dev/img/parallax2.jpg",
        goods_stock_consume: 7,
        order_num: 4,
        goods_stock_reserved: 4,
        goods_stock_purchase: 10,
        goods_supplier: "时刻美",
        goods_price: 2.5
      },
      {
        goods_code: "goods_code 4 ",
        image_url: "https://cdn.quasar.dev/img/parallax2.jpg",
        goods_stock_consume: 5,
        order_num: 10,
        goods_stock_reserved: 2,
        goods_stock_purchase: 12,
        goods_supplier: "斯麦尔",
        goods_price: 3
      },
      {
        goods_code: "goods_code 3 ",
        image_url: "https://cdn.quasar.dev/img/parallax2.jpg",
        goods_stock_consume: 4,
        order_num: 2,
        goods_stock_reserved: 3,
        goods_stock_purchase: 13,
        goods_supplier: "斯麦尔",
        goods_price: 3
      }
    ];
    this.purchasingListStore.addToPurchase(testGoods);

    console.log("on created  this.goodsToPurchaseMap ", this.goodsToPurchase);
    console.log(
      "on created  this.goodsToPurchaseList ",
      this.goodsToPurchaseList
    );
  },
  methods: {
    removeItem(phase, index) {
      this.purchasingListStore.removeItemInPhase(phase, index);
    },
    moveToNexePhase(currentPhase, index) {
      console.log("move to next Phase ", currentPhase, index);
      this.purchasingListStore.moveToNextPhase(currentPhase, index);
    },
    moveToPrePhase(currentPhase, index) {
      console.log("moveToPrePhase ", currentPhase, index);
      let testGoods = [
        {
          goods_code: "goods_code 2 ",
          goods_media_url: "goods_imag_url",
          goods_stock_consume: 7,
          order_num: 4,
          goods_stock_purchase: 10,
          goods_supplier: "时刻美"
        },
        {
          goods_code: "goods_code 2 ",
          goods_media_url: "goods_imag_url",
          goods_stock_consume: 5,
          order_num: 10,
          goods_stock_purchase: 12,
          goods_supplier: "斯麦尔"
        },
        {
          goods_code: "goods_code 3 ",
          goods_media_url: "goods_imag_url",
          goods_stock_consume: 4,
          order_num: 2,
          goods_stock_purchase: 13,
          goods_supplier: "斯麦尔"
        }
      ];
      this.purchasingListStore.addToPurchase(testGoods);
      console.log(
        "after add items this.goodsToPurchaseMap ",
        this.goodsToPurchase
      );
      console.log(
        "after add items this.goodsToPurchaseList",
        this.goodsToPurchaseList
      );
    },
    duplicateItem(currentPhase, index) {
      console.log("dumplicate item ", currentPhase, index);
      this.purchasingListStore.duplicateItem(currentPhase, index);
    },
    onGoodsSelected(goods) {
      console.log(" purchase steps onGoodsSelected ", goods);
      this.newForm = false;
      this.purchasingListStore.addToPurchase(goods);
    }
  },
  components: {
    PurchasingList
  }
};
</script>
