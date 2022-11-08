<template>
  <q-card class="q-mt-md" bordered>
    <template>
      <q-btn-group push>
        <q-btn :label="$t('new')" icon="add" @click="newForm = true">
          <q-tooltip
            content-class="bg-amber text-black shadow-4"
            :offset="[10, 10]"
            content-style="font-size: 12px"
          >
            {{ $t("newtip") }}
          </q-tooltip>
        </q-btn>
        <q-btn :label="$t('refresh')" icon="refresh" @click="reFresh()">
          <q-tooltip
            content-class="bg-amber text-black shadow-4"
            :offset="[10, 10]"
            content-style="font-size: 12px"
          >
            {{ $t("refreshtip") }}
          </q-tooltip>
        </q-btn>
      </q-btn-group>
      <q-space />
      <q-input
        outlined
        rounded
        dense
        debounce="300"
        color="primary"
        v-model="filter"
        :placeholder="$t('search')"
        @blur="getSearchList()"
        @keyup.enter="getSearchList()"
      >
        <template v-slot:append>
          <q-icon name="search" @click="getSearchList()" />
        </template>
      </q-input>
    </template>
    <transition appear enter-active-class="animated fadeIn">
      <ExpandableList
        :listData="tree_list"
        :columns="headers"
        @addCategory="newData"
        @alterCategory="editDataSubmit"
        @deleteCategory="deleteData"
      />
    </transition>
    <q-dialog v-model="newForm">
      <NewGoodsClassDialog
        :parentCategory="newFormParent"
        :parentOptions="table_list"
        @addCategory="newDataSubmit"
        @cancalDialog="newDataCancel"
      >
      </NewGoodsClassDialog>
    </q-dialog>

    <q-dialog v-model="deleteForm">
      <q-card class="shadow-24">
        <q-bar
          class="bg-light-blue-10 text-white rounded-borders"
          style="height: 50px"
        >
          <div>{{ $t("delete") }}</div>
          <q-space />
          <q-btn dense flat icon="close" v-close-popup>
            <q-tooltip>{{ $t("index.close") }}</q-tooltip>
          </q-btn>
        </q-bar>
        <q-card-section style="max-height: 325px; width: 400px" class="scroll">
          {{ $t("deletetip") }}
        </q-card-section>
        <div style="float: right; padding: 15px 15px 15px 0">
          <q-btn
            color="white"
            text-color="black"
            style="margin-right: 25px"
            @click="deleteDataCancel()"
            >{{ $t("cancel") }}</q-btn
          >
          <q-btn color="primary" @click="deleteDataSubmit()">{{
            $t("submit")
          }}</q-btn>
        </div>
      </q-card>
    </q-dialog>
  </q-card>
</template>
<router-view />

<script>
import { getauth, postauth, putauth, deleteauth } from "boot/axios_request";
import { goodsClass2Tree } from "boot/utils";
import ExpandableList from "./components/expandableList";
import NewGoodsClassDialog from "./components/newGoodsClassDialog.vue";

export default {
  name: "Pagegoodsclass",
  data() {
    return {
      openid: "",
      login_name: "",
      authin: "0",
      pathname: "goodsclass/",
      loading: false,
      height: "",
      table_list: [],
      tree_list: [],
      headers: ["name", "creater", "create_time", "update_time", "action"],
      filter: "",
      newForm: false,
      editid: 0,
      editFormData: {},
      editMode: false,
      deleteForm: false,
      deleteids: [],
      error1: this.$t("goods.view_class.error1"),
      newFormParent: undefined,
    };
  },
  methods: {
    getList() {
      var _this = this;
      if (_this.$q.localStorage.has("auth")) {
        getauth(_this.pathname, {})
          .then(res => {
            _this.table_list = res.results;
            _this.tree_list = goodsClass2Tree(res.results);
          })
          .catch(err => {
            _this.$q.notify({
              message: err.detail,
              icon: "close",
              color: "negative"
            });
          });
      } else {
      }
    },
    getSearchList() {
      var _this = this;
      if (_this.$q.localStorage.has("auth")) {
        getauth(_this.pathname + "?goods_class__icontains=" + _this.filter, {})
          .then(res => {
            _this.table_list = res.results;
          })
          .catch(err => {
            _this.$q.notify({
              message: err.detail,
              icon: "close",
              color: "negative"
            });
          });
      } else {
      }
    },
    reFresh() {
      var _this = this;
      _this.getList();
    },
    newData(parent_id) {
      var _this = this;
      if (parent_id != null) {
        _this.newFormParent = this.table_list.find(item => {
          return item.id == parent_id;
        });
      } else {
        t_thishis.newFormParent = undefined;
      }
      _this.newForm = true;
    },
    newDataSubmit(parents_class_id, class_name) {
      var _this = this;
      var goodsclasses = [];
      _this.table_list.forEach(i => {
        goodsclasses.push(i.goods_class);
      });
      if (goodsclasses.indexOf(class_name) === -1 && class_name.length !== 0) {
        let newClassData = {
          goods_class: class_name,
          parents_class_id: parents_class_id,
          creater:  _this.login_name
        };
        console.log("posting new class ", newClassData)
        postauth(_this.pathname, newClassData)
          .then(res => {
            _this.getList();
            _this.$q.notify({
              message: "Success Create",
              icon: "check",
              color: "green"
            });
          })
          .catch(err => {
            _this.$q.notify({
              message: err.detail,
              icon: "close",
              color: "negative"
            });
          });
      } else if (goodsclasses.indexOf(class_name) !== -1) {
        _this.$q.notify({
          message: _this.$t("notice.goodserror.goods_classerror"),
          icon: "close",
          color: "negative"
        });
      } else if (class_name.length === 0) {
        _this.$q.notify({
          message: _this.$t("goods.view_class.error1"),
          icon: "close",
          color: "negative"
        });
      }
      goodsclasses = [];
    },
    newDataCancel() {
      var _this = this;
      _this.newForm = false;
      _this.newFormParent=null;
    },
    editDataSubmit(id, name) {
      var _this = this;
      let formData = {
        goods_class: name,
        creater: _this.login_name
      };
      putauth(_this.pathname + id + "/", formData)
        .then(res => {
          _this.getList();
          _this.$q.notify({
            message: "Success Edit Data",
            icon: "check",
            color: "green"
          });
        })
        .catch(err => {
          _this.$q.notify({
            message: err.detail,
            icon: "close",
            color: "negative"
          });
        });
    },
    editDataCancel() {
      var _this = this;
      _this.editMode = false;
      _this.editid = 0;
      _this.editFormData = {
        goods_class: "",
        creater: ""
      };
    },
    deleteData(ids) {
      var _this = this;
      _this.deleteForm = true;
      _this.deleteids = ids;
    },
    deleteDataSubmit() {
      var _this = this;
      function deleteauthRecursive(ids) {
        if (ids.length <= 0) {
          _this.getList();
          _this.deleteDataCancel();
          _this.$q.notify({
            message: "Success Edit Data",
            icon: "check",
            color: "green"
          });
        } else {
          let id = ids.pop();
          console.log("try to delete id ", id);
          deleteauth(_this.pathname + id + "/")
            .then(res => {
              console.log("delete id success ", id);
              deleteauthRecursive(ids);
            })
            .catch(err => {
              _this.$q.notify({
                message: err.detail,
                icon: "close",
                color: "negative"
              });
            });
        }
      }
      console.log("deletes category ", _this.deleteids);
      deleteauthRecursive(_this.deleteids);
    },
    deleteDataCancel() {
      var _this = this;
      _this.deleteForm = false;
      _this.deleteid = [];
    }
  },
  created() {
    var _this = this;
    if (_this.$q.localStorage.has("openid")) {
      _this.openid = _this.$q.localStorage.getItem("openid");
    } else {
      _this.openid = "";
      _this.$q.localStorage.set("openid", "");
    }
    if (_this.$q.localStorage.has("login_name")) {
      _this.login_name = _this.$q.localStorage.getItem("login_name");
    } else {
      _this.login_name = "";
      _this.$q.localStorage.set("login_name", "");
    }
    if (_this.$q.localStorage.has("auth")) {
      _this.authin = "1";
      _this.getList();
    } else {
      _this.authin = "0";
    }
  },
  mounted() {
    var _this = this;
    if (_this.$q.platform.is.electron) {
      _this.height = String(_this.$q.screen.height - 290) + "px";
    } else {
      _this.height = _this.$q.screen.height - 290 + "" + "px";
    }
  },
  updated() {},
  destroyed() {},
  components: { ExpandableList, NewGoodsClassDialog, NewGoodsClassDialog }
};
</script>
