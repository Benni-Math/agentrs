use rustc_hash::FxHashMap;

use crate::operation::Operation;

/// Main API (rough outline)
/// TODO: add PyO3 types
trait ModelFrame {
    fn new(parameters: Option<>, _run_id: Option<usize>, forwarded_args: Option<>) -> Self;
    fn stop();
}


pub struct Model {
    name: String,
    // TODO: what number type to use?
    // What about floats? Or just stick to integers?
    // Are properties not specific to Agents?
    properties: FxHashMap<&str, i64>,
    // TODO: also need parameters?
    parameters: FxHashMap<&str, f64>,
    // TODO: something more efficient than Vec<Agent>?
    operations: Vec<Operation>,
}

struct ModelBuilder {
    name: String,
    properties: FxHashMap<&str, i64>,
    parameters: FxHashMap<&str, f64>,
    operations: Vec<Operation>,
}

impl Model {
    fn builder(name: String) -> ModelBuilder {
        ModelBuilder::new(name)
    }
}

// TODO: builder should accept Python equivalents
impl ModelBuilder {
    fn new(name: String) -> Self {
        Self {
            name: name,
            parameters: FxHashMap::new(),
            properties: FxHashMap::new(),
            operations: Vec::new(),
        }
    }

    fn build(&self) -> Model {

    }
}
