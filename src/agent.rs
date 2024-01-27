use std::sync::Arc;

use pyo3::PyAny;
use rustc_hash::FxHashMap;

// use crate::operation::Operation;
// use crate::model::Model;

pub struct Agent<'a> {
    // TODO: change to Model after implementing in Rust
    model: Arc<PyAny>,
    // TODO: eventually make it so the `properties` is only on the factory
    // and then we have a method of 'saving' so that the Agent just has a Vec
    // along with a method of translating from property name to index
    // a 'perfect' hashmap, or rather a trie or a flatbuffer
    // https://www.reddit.com/r/rust/comments/126k7zq/creating_a_perfect_hashmap_from_string_keys_known/
    properties: FxHashMap<&'static str, i64>,
    // operations: &'a Vec<Operation<'a>>,
    // FIXME: is this even necessary?
    operations: FxHashMap<&'static str,&'a PyAny>,
}

impl Agent<'_> {
    pub fn new<'a>(model: Arc<PyAny>, properties: FxHashMap<&'static str, i64>) -> Self {
        Agent {
            model,
            properties,
            operations: FxHashMap::default(),
        }
    }

    pub fn get_property(&self, key: &str) -> Option<i64> {
        self.properties.get(key).copied()
    }

    // TODO: this shouldn't be dynamically added, definitely inefficient
    // create factory method that takes pre-determined class
    // pull the operations from the class methods (maybe?)
    pub fn add_operation<'a>(&mut self, op_name: &'static str, op: &'static PyAny) -> &Self {
        if !PyAny::is_callable(op) {
            panic!("(agentrs) Operation added was not a callable Python object.")
        }
        self.operations.insert(op_name, op);
        self
    }
}
