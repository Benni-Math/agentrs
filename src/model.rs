use rustc_hash::FxHashMap;

use crate::operation::Operation;

/// Main API (rough outline)
/// TODO: add PyO3 types
trait ModelFrame<'a> {
    fn new(parameters: FxHashMap<&'a str, &'a str>, _run_id: Option<usize>, forwarded_args: FxHashMap<&'a str, &'a str>) -> Self;
    fn stop();
}


pub struct Model<'a> {
    name: String,
    // TODO: what number type to use?
    // What about floats? Or just stick to integers?
    // Are properties not specific to Agents?
    properties: FxHashMap<&'a str, i64>,
    // TODO: also need parameters?
    parameters: FxHashMap<&'a str, f64>,
    // TODO: something more efficient than Vec<Agent>?
    operations: Vec<Operation<'a>>,
}

struct ModelBuilder<'a> {
    name: String,
    properties: FxHashMap<&'a str, i64>,
    parameters: FxHashMap<&'a str, f64>,
    operations: Vec<Operation<'a>>,
}

impl Model<'_> {
    fn builder(name: String) -> ModelBuilder<'static> {
        ModelBuilder::new(name)
    }
}

// TODO: builder should accept Python equivalents
impl<'a> ModelBuilder<'a> {
    fn new(name: String) -> Self {
        Self {
            name,
            parameters: FxHashMap::default(),
            properties: FxHashMap::default(),
            operations: Vec::new(),
        }
    }

    fn build(self) -> Model<'a> {
        Model {
            name: self.name.clone(),
            parameters: self.parameters,
            properties: self.properties,
            operations: self.operations,
        }
    }
}
