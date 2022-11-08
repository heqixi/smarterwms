<template>
  <q-list bordered class="rounded-borders">
    <div class="row">
      <div class="col">
        <div class="q-pl-md">
          名称
        </div>
      </div>
      <div class="col">
        创建者
      </div>
      <div class="col">
        创建时间
      </div>
      <div class="col">
        <div class="q-pl-lg q-ml-lg">
          编辑
        </div>
      </div>
    </div>
    <q-expansion-item v-for="(rootItem, index) in listData" :key="index">
      <template v-slot:header>
        <q-item-section>
          <div v-if="editId !== rootItem.id">
            {{ rootItem.goods_class }}
          </div>
          <div v-else>
            <q-input
              dense
              outlined
              square
              v-model="rootItem.goods_class"
              :label="$t('goods.view_goodslist.goods_class')"
              autofocus
              :rules="[val => (val && val.length > 0) || error1]"
              @keydown.enter="editCategorySummit(rootItem)"
            />
          </div>
        </q-item-section>
        <q-item-section>
          {{ rootItem.creater }}
        </q-item-section>
        <q-item-section>
          {{ rootItem.create_time }}
        </q-item-section>
        <q-item-section>
          <div v-if="editId !== rootItem.id" class="row">
            <div class="col">
              <q-btn
                round
                color="primary"
                icon="add"
                @click.stop="addCategory(rootItem.id)"
              />
            </div>
            <div class="col">
              <q-btn
                round
                color="primary"
                icon="edit"
                @click.stop="updateCategory(rootItem.id)"
              />
            </div>
            <div class="col">
              <q-btn
                round
                color="primary"
                icon="delete"
                @click.stop="deleteCategory(rootItem)"
              />
            </div>
          </div>
          <div v-else class="row">
            <div class="col">
              <q-btn
                round
                color="primary"
                icon="check"
                @click.stop="editCategorySummit(rootItem)"
              />
            </div>
            <div class="col">
              <q-btn
                round
                color="primary"
                icon="close"
                @click.stop="editId = -1"
              />
            </div>
          </div>
        </q-item-section>
      </template>

      <q-list v-if="rootItem.children" bordered class="rounded-borders">
        <q-expansion-item
          v-for="(firstLevelItem, index) in rootItem.children"
          :key="index"
        >
          <template v-slot:header>
            <q-item-section>
              <div class="q-pl-md q-ml-sm">
                <div v-if="editId !== firstLevelItem.id">
                  {{ firstLevelItem.goods_class }}
                </div>
                <div v-else>
                  <q-input
                    dense
                    outlined
                    square
                    v-model="firstLevelItem.goods_class"
                    :label="$t('goods.view_goodslist.goods_class')"
                    autofocus
                    :rules="[val => (val && val.length > 0) || error1]"
                    @keydown.enter="editCategorySummit(firstLevelItem)"
                  />
                </div>
              </div>
            </q-item-section>
            <q-item-section>
              {{ firstLevelItem.creater }}
            </q-item-section>
            <q-item-section>
              {{ firstLevelItem.create_time }}
            </q-item-section>
            <q-item-section>
              <div class="row" v-if="editId !== firstLevelItem.id">
                <div class="col">
                  <q-btn
                    round
                    color="primary"
                    icon="add"
                    @click.stop="addCategory(firstLevelItem.id)"
                  />
                </div>
                <div class="col">
                  <q-btn
                    round
                    color="primary"
                    icon="edit"
                    @click.stop="updateCategory(firstLevelItem.id)"
                  />
                </div>
                <div class="col">
                  <q-btn
                    round
                    color="primary"
                    icon="delete"
                    @click.stop="deleteCategory(firstLevelItem)"
                  />
                </div>
              </div>
              <div v-else class="row">
                <div class="col">
                  <q-btn
                    round
                    color="primary"
                    icon="check"
                    @click.stop="editCategorySummit(firstLevelItem)"
                  />
                </div>
                <div class="col">
                  <q-btn
                    round
                    color="primary"
                    icon="close"
                    @click.stop="editId = -1"
                  />
                </div>
              </div>
            </q-item-section>
          </template>
          <q-list bordered class="rounded-borders">
            <q-expansion-item
              v-for="(secondLevelItem, index) in firstLevelItem.children"
              :key="index"
            >
              <template v-slot:header>
                <q-item-section>
                  <div class="q-pl-lg q-ml-lg">
                    <div v-if="editId !== secondLevelItem.id">
                      {{ secondLevelItem.goods_class }}
                    </div>
                    <div v-else>
                      <q-input
                        dense
                        outlined
                        square
                        v-model="secondLevelItem.goods_class"
                        :label="$t('goods.view_goodslist.goods_class')"
                        autofocus
                        :rules="[val => (val && val.length > 0) || error1]"
                        @keydown.enter="editCategorySummit(firstLevelItem)"
                      />
                    </div>
                  </div>
                </q-item-section>
                <q-item-section>
                  {{ secondLevelItem.creater }}
                </q-item-section>
                <q-item-section>
                  {{ secondLevelItem.create_time }}
                </q-item-section>
                <q-item-section>
                  <div class="row" v-if="editId !== secondLevelItem.id">
                    <div class="col">
                      <!-- <q-btn
                        round
                        color="primary"
                        icon="add"
                        @click.stop="addCategory(secondLevelItem.id)"
                      /> -->
                    </div>
                    <div class="col">
                      <q-btn
                        round
                        color="primary"
                        icon="edit"
                        @click.stop="updateCategory(secondLevelItem.id)"
                      />
                    </div>
                    <div class="col">
                      <q-btn
                        round
                        color="primary"
                        icon="delete"
                        @click.stop="deleteCategory(secondLevelItem)"
                      />
                    </div>
                  </div>
                  <div v-else class="row">
                    <div class="col">
                      <q-btn
                        round
                        color="primary"
                        icon="check"
                        @click.stop="editCategorySummit(secondLevelItem)"
                      />
                    </div>
                    <div class="col">
                      <q-btn
                        round
                        color="primary"
                        icon="close"
                        @click.stop="editId = -1"
                      />
                    </div>
                  </div>
                </q-item-section>
              </template>
            </q-expansion-item>
          </q-list>
        </q-expansion-item>
      </q-list>
    </q-expansion-item>
  </q-list>
</template>

<script>

export default {
  name: "ExpandableList",
  data() {
    return {
      editId: -1
    };
  },
  methods: {
    addCategory(parent_id) {
      this.$emit("addCategory", parent_id);
    },
    updateCategory(id) {
      this.editId = id;
      this.$emit("updateCategory");
    },
    deleteCategory(item) {
      let deleteIds = [];
      function recursiveGetIds(item, idArray) {
        if (item == null) {
          return;
        }
        idArray.push(item.id);
        if (item.children) {
          item.children.forEach(item => {
            recursiveGetIds(item, idArray);
          });
        }
      }
      recursiveGetIds(item, deleteIds);
      this.$emit("deleteCategory", deleteIds);
    },
    editCategorySummit(item) {
      this.editId = -1;
      this.$emit('alterCategory', item.id, item.goods_class);
    }
  },
  props: ["listData", "columns"],
};
</script>
