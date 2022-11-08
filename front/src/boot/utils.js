/**
 *
 * @param classList 类别的列表
 * @returns 类别树(森林)
 *
 * For example, when
 * classList = [
  {
    parents_class_id:"",
    id:0,
    name:"watch"
  },
  {
    parents_class_id:"0",
    id:1,
    name:"menwatch"
  },
  {
    id:2,
    parents_class_id:"0",
    name:"womenwatch"
  },
  {
    id:4,
    parents_class_id:"2",
    name:"digitalwomenwatch"
  },
  {
    parents_class_id:"",
    id:5,
    name:"clothes"
  },
  {
    parents_class_id:"5",
    id:6,
    name:"menclothes"
  },
  {
    parents_class_id:"5",
    id:7,
    name:"womenclothes"
  }
],
   Then the output should be :
   [
    {
    parents_class_id:"",
    id:0,
    name:"watch",
    children: {
        {
          parents_class_id:"0",
          id:1,
          name:"menwatch"
        },
        {
          id:2,
          parents_class_id:"0",
          name:"womenwatch",
          children: {
            id:4,
            parents_class_id:"2",
            name:"digitalwomenwatch"
          }
        },
    },
    {
    parents_class_id:"",
    id:5,
    name:"clothes",
    children:{
      {
        parents_class_id:"5",
        id:6,
        name:"menclothes"
      },
      {
        parents_class_id:"5",
        id:7,
        name:"womenclothes"
      }
    }
   ]
 */
function goodsClass2Tree(classList) {
  let roots = classList.filter((item, index) => {
    return (
      item.parents_class_id == undefined || item.parents_class_id.length <= 0
    );
  });
  let itemBulk = [];
  classList.forEach(function(item) {
    itemBulk[item.id] = item;
  });
  itemBulk.forEach(item => {
    if (
      item != undefined &&
      item.parents_class_id &&
      item.parents_class_id.length > 0 &&
      itemBulk[item.parents_class_id]
    ) {
      let parent = itemBulk[item.parents_class_id];
      if (parent.children) {
        parent.children.push(item);
      } else {
        parent.children = [item];
      }
    }
  });
  console.log("root string ", JSON.stringify(roots));
  return roots;
}

function allNotEmptyOrPositive(...exams) {
  console.log("exams ", exams);
  return exams.reduce((total, exam) => {
    return total && notEmptyOrPositive(exam);
  }, true);
}

function notEmptyOrPositive(data) {
  if (data == undefined || data == null) {
    return false;
  }
  if (typeof data == "string") {
    return data != "";
  }
  if (typeof data == "number") {
    return data > 0;
  }
  if (data instanceof Array) {
    return data.length > 0;
  }
  return false;
}

export { goodsClass2Tree, notEmptyOrPositive, allNotEmptyOrPositive};
