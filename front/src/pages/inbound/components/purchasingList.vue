<template>
  <div>
    <!-- <q-banner inline-actions class="bg-blue-6">{{ phase }} </q-banner> -->
    <q-virtual-scroll
      type="table"
      style="max-height: 70vh"
      :virtual-scroll-item-size="48"
      :virtual-scroll-sticky-size-start="48"
      :virtual-scroll-sticky-size-end="32"
      :items="items"
    >
      <template v-slot:before>
        <thead class="thead-sticky text-left">
          <tr>
            <th></th>
            <!--  头部 -->
            <th v-for="col in columns" :key="'1--' + col.name" :style="col.style">
              <div class="text-weight-bold">
                {{ col.label }}
              </div>
            </th>
          </tr>
        </thead>
      </template>

      <template v-slot="{ item: row, rowIndex }">
        <tr :key="rowIndex">
          <q-td auto-width>
            <q-toggle
              v-model="expandItems[row.id]"
              checked-icon="add"
              unchecked-icon="remove"
            />
          </q-td>
          <td v-for="col in columns" :key="rowIndex + '-' + col.name">
            <div v-if="col.name === 'action'">
              <q-btn-group>
                <q-btn color="primary" @click="nextPhase(row.id)"
                  >{{ nextBtnLabel()}}
                </q-btn>
                <!-- <q-btn
                  color="accent"
                  icon="content_copy"
                  @click="dumplicate(row.id)"
                /> -->
                <q-btn color="red" icon="delete" @click="itemRemove(row.id)" />
              </q-btn-group>
            </div>
            <div v-if="col.type == 'url'">
              <a
                v-if="_getFieldValue(row, col)"
                :href="_getFieldValue(row, col)"
                >访问</a
              >
              <div v-else>
                未知
              </div>
            </div>
            <div v-else>
              {{ _getFieldValue(row, col) }}
            </div>
          </td>
        </tr>
        <!-- 展开的 Header -->
        <tr v-show="expandItems[row.id]">
          <td v-for="(column, head_index) in expandColumns" :key="head_index">
            {{ column.label }}
          </td>
        </tr>
        <!-- 展开的 数据 -->
        <tr
          v-show="expandItems[row.id]"
          v-for="(expandItem, goodsIndex) in row[expandField]"
          :key="'goods-' + Math.round(Math.random() * 1000) + goodsIndex"
        >
          <td v-for="(col, col_index) in expandColumns" :key="col_index">
            <div v-if="col.type == 'image'">
              <q-img
                :src="_getFieldValue(expandItem, col)"
                spinner-color="white"
                style="height: 80px; min-width: 80px; max-width: 200px"
                img-class="my-custom-image"
                class="rounded-borders"
              />
            </div>
            <div v-if="col.type == 'string' || col.type == 'number'">
              <q-input
                v-if="
                  col.edit &&
                    row.id == editItem.rowId &&
                    expandItem.id == editItem.subRowId &&
                    col.name == editItem.fieldName
                "
                class="q-pt-md"
                style="max-width:80px"
                dense
                outlined
                square
                autofocus
                v-model="newFieldForm.value"
                :type="col.type"
                :label="col.label"
                :rules="[val => (val && val > 0) || '采购数量须大于0']"
                @keyup.enter="_onFieldUpdated"
              />
              <div
                v-else
                @click="
                  _fieldEdit(
                    row.id,
                    expandItem.id,
                    col.name,
                    _getFieldValue(expandItem, col)
                  )
                "
              >
                <q-badge
                  v-if="col.edit"
                  class="q-mt-sm q-mr-lg"
                  color="red"
                  floating
                  transparent
                >
                  edit
                </q-badge>
                {{ _getFieldValue(expandItem, col) }}
              </div>
            </div>
            <div v-if="col.type == 'url'">
              <a :href="_getFieldValue(expandItem, col)">点击前往</a>
            </div>
          </td>

          <td>
            <q-btn-group>
              <q-btn
                color="red"
                icon="delete"
                @click="goodsRemove(rowIndex, goodsIndex)"
              />
            </q-btn-group>
          </td>
        </tr>

        <q-separator />
      </template>
    </q-virtual-scroll>
  </div>
</template>

<script>
import { PHASE_TYPE } from "../../../store/inbound/types";

export default {
  name: "PurchasingList",
  data() {
    return {
      expandItems: [],
      editItem: {
        phaseType: this.phase,
        rowId: -1,
        subRowId: -1,
        fieldName: "",
        value: undefined
      },
      newFieldForm: undefined,
      searchDialog: false,
      unOrder: true,
      button_next: "确定"
    };
  },
  methods: {
    nextBtnLabel() {
      console.log("this.phase ",this.phase);
      // return "去采购";
      if (this.phase == PHASE_TYPE.purchase) {
        return "去采购";
      }
    },
    deepCopyVuexState(value) {
      return JSON.parse(JSON.stringify(value));
    },
    _getFieldValue(item, column) {
      let targetField = item;
      if (column.field != "self") {
        targetField = item[column.field];
      }
      let value = column.fieldMap ? column.fieldMap(targetField) : targetField;
      return value;
    },
    _onFieldUpdated(evt) {
      console.log("_onFieldUpdated start", this.editItem, this.newFieldForm);
      this.$emit("onFieldUpdated", this.newFieldForm);
      this._resetEditItem();
    },
    _fieldEdit(row_id, subrow_id, field_name, value) {
      console.log("_fieldEdit, data ", row_id, subrow_id, field_name, value);
      this.editItem.rowId = row_id;
      this.editItem.subRowId = subrow_id;
      this.editItem.fieldName = field_name;
      this.editItem.value = value;
      this.newFieldForm = {
        phase: this.phase,
        row_id: row_id,
        subrow_id: subrow_id,
        field_name: field_name,
        value: value
      };
      console.log("this editItem ", this.newFieldForm);
      this.$emit("fieldEdit", row_id, field_name);
    },

    itemSave(index) {
      console.log("item save ", index);
      this.$emit("itemSave", this.phase, index);
    },
    itemRemove(id) {
      this.$emit("itemRemove", id);
    },
    nextPhase(index) {
      this.$emit("nextPhase", this.phase, index);
    },
    prePhase(index) {
      this.$emit("prePhase", this.phase, index);
    },
    dumplicate(index) {
      this.$emit("dumplicate", this.phase, index);
    },
    goodsRemove(supplierIndex, goodsIndex) {
      console.log("goods remove ", supplierIndex, " ", goodsIndex);
    },
    _resetEditItem() {
      console.log("_resetEditItem start");
      this.editItem.rowId = -998;
      this.editItem.subRowId = -999;
      this.editItem.fieldName = "reset";
      this.editItem.value = undefined;
      console.log("_resetEditItem end");
    }
  },
  created() {
    this.items.forEach(item => {
      this.expandItems[item.id] = false;
    });
    console.log("purchase List on create ", this.items);
  },
  props: [
    "title",
    "items",
    "phase",
    "actionLabel",
    "columns",
    "expandField",
    "expandColumns"
  ]
};
</script>

<style lang="sass">
.thead-sticky tr > *,
.tfoot-sticky tr > *
  position: sticky
  opacity: 1
  z-index: 1
  background: gray
  color: white

.thead-sticky tr:last-child > *
  top: 0

.tfoot-sticky tr:first-child > *
  bottom: 0
</style>
